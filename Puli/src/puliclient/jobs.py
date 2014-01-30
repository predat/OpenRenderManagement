'''
Created on Jan 11, 2010

@author: Olivier Derpierre
'''

import sys
import traceback
import logging

class CommandError(Exception):
    '''Raised to signal failure of a CommandRunner execution.'''

class ValidationError(CommandError):
    '''Raised on a validation error'''

class RangeError(CommandError):
    '''Raised on a validation error where a value given is out of authorized range'''

class JobTypeImportError(ImportError):
    '''Raised when an error occurs while loading a job type through the load function'''

class CommandRunnerParameter(object):
    '''Base class for formal command runner parameter.'''

    name = None
    isMandatory = False

    def __init__(self, default=None, mandatory=None, **kwargs):
        if default is not None:
            self.hasDefault = True
            self.defaultValue = default
        else:
            self.hasDefault = False
            self.defaultValue = None

        if mandatory is not None:
            self.isMandatory = True

        # Set range values if given in args, still need to be validated against value
        # TODO specialize it in typed parameter classes
        if 'min' in kwargs:
            self.minValue = kwargs['min']
        if 'max' in kwargs:
            self.maxValue = kwargs['max']


    def validate(self, arguments):
        if not self.name in arguments and self.isMandatory:
            raise ValidationError("Mandatory argument \"%s\" is not defined in command arguments" % self.name)

        if not self.name in arguments and self.hasDefault:
            arguments[self.name] = self.defaultValue


    def __repr__(self):
        return "CommandRunnerParameter(name=%r, default=%r, mandatory=%r)" % (self.name, self.defaultValue, self.isMandatory)

    def __str__(self):
        return "%r (default=%r, mandatory=%r)" % (self.name, self.defaultValue, self.isMandatory)


class StringParameter(CommandRunnerParameter):
    '''A command runner parameter class that converts the argument value to a string.'''

    def validate(self, arguments):

        try:
            super(StringParameter, self).validate(arguments)
            if arguments[self.name]:
                # try:
                arguments[self.name] = str(arguments[self.name])
                # except Exception, e:
                #     print "Error when parameter conversion %s: %r" % (self.name, e)
                #     raise ValidationError("StringParameter cannot be converted to str")
        except Exception, e:
            raise e

    # def __repr__(self):
    #     return "StringParameter(name=%r, default=%r, mandatory=%r)" % (self.name, self.defaultValue, self.isMandatory)

class StringListParameter(CommandRunnerParameter):

    def validate(self, arguments):
        try:
            super(StringListParameter, self).validate(arguments)

            arguments[self.name] = [str(v) for v in arguments[self.name]]
        except Exception, e:
            raise e

class BooleanParameter(CommandRunnerParameter):

    def validate(self, arguments):
        try:
            super(BooleanParameter, self).validate(arguments)
            arguments[self.name] = bool(arguments[self.name])
        except Exception, e:
            raise e

class IntegerParameter(CommandRunnerParameter):
    '''A command runner parameter class that converts the argument value to an integer value.'''

    minValue = None
    maxValue = None

    def validate(self, arguments):
        try:
            # Base class will check if argument is present or ensure it has its default value
            super(IntegerParameter, self).validate(arguments)

            if arguments[self.name]:
                newVal = int(arguments[self.name])
                # Validate range if defined
                if self.minValue is not None and newVal < self.minValue:
                    raise RangeError("Argument \"%s\"=%d is less than minimum: %d" % (
                                        self.name, 
                                        newVal, 
                                        self.minValue) )

                if self.maxValue is not None and self.maxValue < newVal:
                    raise RangeError("Argument \"%s\"=%d is more than maximum: %d" % (
                                        self.name, 
                                        self.maxValue,
                                        newVal ) )

                arguments[self.name] = newVal
        except Exception, e:
            raise e

    def __repr__(self):
        return "IntParameter(name=%r, default=%r, mandatory=%r, minValue=%r, maxValue=%r )" % (
                    self.name, 
                    self.defaultValue, 
                    self.isMandatory,
                    self.minValue,
                    self.maxValue,
                    )

    def __str__(self):
        return "%r (default=%r, mandatory=%r, range=[%r,%r])" % (self.name, self.defaultValue, self.isMandatory, self.minValue, self.maxValue)

class FloatParameter(CommandRunnerParameter):
    '''A command runner parameter class that converts the argument value to an float value.'''

    minValue = None
    maxValue = None

    def validate(self, arguments):
        try:
            super(FloatParameter, self).validate(arguments)
            
            if arguments[self.name]:
                newVal = float(arguments[self.name])
                # Validate range if defined
                if self.minValue is not None and newVal < self.minValue:
                    raise RangeError("Argument \"%s\"=%d is less than minimum: %d" % (
                                        self.name, 
                                        newVal, 
                                        self.minValue) )

                if self.maxValue is not None and self.maxValue < newVal:
                    raise RangeError("Argument \"%s\"=%d is more than maximum: %d" % (
                                        self.name, 
                                        self.maxValue,
                                        newVal ) )

                arguments[self.name] = newVal

        except Exception, e:
            raise e

    def __repr__(self):
        return "FloatParameter(name=%r, default=%r, mandatory=%r, minValue=%r, maxValue=%r )" % (
                    self.name, 
                    self.defaultValue, 
                    self.isMandatory,
                    self.minValue,
                    self.maxValue,
                    )

    def __str__(self):
        return "%r (default=%r, mandatory=%r, range=[%r,%r])" % (self.name, self.defaultValue, self.isMandatory, self.minValue, self.maxValue)



class CommandRunnerMetaclass(type):

    def __init__(self, name, bases, attributes):
        type.__init__(self, name, bases, attributes)
        parameters = attributes.get('parameters', [])
        for base in bases:
            if isinstance(base, CommandRunnerMetaclass):
                parameters += base.parameters
        for (name, arg) in attributes.iteritems():
            if isinstance(arg, CommandRunnerParameter):
                arg.name = name
                parameters.append(arg)
        self.parameters = parameters

class CommandRunner(object):

    __metaclass__ = CommandRunnerMetaclass

    scriptTimeOut = None
    parameters = []


    def execute(self, arguments, updateCompletion, updateMessage):
        raise NotImplementedError

    def validate(self, arguments):
        logger = logging.getLogger('puli.commandwatcher')
        if len(self.parameters) > 0:
            logger.info("Validating %d parameter(s):" % len(self.parameters))

        for parameter in self.parameters:
            logger.info("  - %s" % parameter)
            parameter.validate(arguments)

class DefaultCommandRunner(CommandRunner):
    
    cmd = StringParameter( mandatory = True )
    timeout = IntegerParameter( default=0 )

    def __init__( self ):
        super(DefaultCommandRunner, self).__init__( task )
        pass

    def execute(self, arguments, updateCompletion, updateMessage):
        '''
        | Simple execution using the helper. Default argument "cmd" is expected (mandatory)
        | to start the execution with the current env.
        '''
        cmd = arguments[ 'cmd' ]
        timeout = arguments['timeout']

        print 'Running command "%s"' % cmd
        helper = PuliActionHelper(cleanTemp=True)

        updateCompletion(0)

        if arguments['timeout'] == 0:
            helper.execute( cmd.split(" "), env=os.environ )
        else:
            helper.executeWithTimeout( cmd.split(" "), env=os.environ, timeout )

        updateCompletion(1)


class TaskExpander(object):

    def __init__(self, taskGroup):
        pass

class TaskDecomposer(object):
    """
    | Base class for Decomposer hierarchy.
    | Implements a minimalist "addCommand" method.
    """

    def __init__(self, task):
        self.task = task

    def addCommand(self, name, args):
        self.task.addCommand(name, args)

class DefaultTaskDecomposer(TaskDecomposer):
    """
    | Default decomposesr called when no decomposer given for a task. It will use the PuliActionHelper to create one
    | or several commands on a task. PuliActionHelper's decompose method will have the following behaviour:
    |   - if "framesList" is defined: 
    |         create a command for each frame indicated (frameList is a string with frame numbers separated by spaces)
    |   - else:
    |         try to use start/end/packetSize attributes to create several commands (frames grouped by packetSize)
    |
    | If no "arguments" dict is given, print a warning and create a single command with empty arguments.
    """

    # DEFAULT FIELDS USED TO DECOMPOSE A TASK
    START_LABEL="start"
    END_LABEL="end"
    PACKETSIZE_LABEL="packetSize"
    FRAMESLIST_LABEL="framesList"

    def __init__(self, task):
        super(DefaultTaskDecomposer, self).__init__(task)

        if task.arguments is not None:
            start = ( task.arguments[self.START_LABEL] if self.START_LABEL in task.arguments.keys() else 1 )
            end = ( task.arguments[self.END_LABEL] if self.END_LABEL in task.arguments.keys() else 1 )
            packetSize = ( task.arguments[self.PACKETSIZE_LABEL] if self.PACKETSIZE_LABEL in task.arguments.keys() else 1 )
            framesList = ( task.arguments[self.FRAMESLIST_LABEL] if self.FRAMESLIST_LABEL in task.arguments.keys() else "" )

            # print "Decompose args: start=%r, end=%r, packetSize=%r, callback=%r, frameList=%s" % (start, end, packetSize, self, framesList)

            from puliclient.contrib.helper.helper import PuliActionHelper
            PuliActionHelper().decompose( start=start, end=end, packetSize=packetSize, callback=self, framesList=framesList )

        else:
            # Create an empty command anyway --> probably unecessary
            print "WARNING: No arguments given for the task \"%s\", it is necessary to do this ? (we are creating an empty command anyway..." % task.name
            self.addCommand(task.name+"_1_1", {})


    def addCommand(self, packetStart, packetEnd):
        '''
        Default method to add a command with this TaskDecomposer.

        :param packetStart: Integer representing the first frame
        :param packetEnd: Integer representing the last frame
        '''
        cmdArgs = self.task.arguments.copy()
        cmdArgs[self.START_LABEL] = packetStart
        cmdArgs[self.END_LABEL] = packetEnd

        cmdName = "%s_%s_%s" % (self.task.name, str(packetStart), str(packetEnd))
        self.task.addCommand(cmdName, cmdArgs)







def _load(name, motherClass):
    try:
        moduleName, cls = name.rsplit(".", 1)
    except ValueError:
        raise JobTypeImportError("Invalid job type name '%s'. It should be like 'some.module.JobClassName'." % name)

    try:
        module = __import__(moduleName, fromlist=[cls])
    except ImportError, error:
        traceback.print_exc()
        raise JobTypeImportError("No module '%s' on PYTHONPATH:\n%s. (%s)" % (moduleName, "\n".join(sys.path), error))

    try:
        jobtype = getattr(module, cls)
    except AttributeError:
        raise JobTypeImportError("No such job type '%s' defined in module '%s'." % (cls, name))

    if not issubclass(jobtype, motherClass):
        motherClassName = "%s.%s" % (motherClass.__module__, motherClass.__name__)
        raise JobTypeImportError("%s (loaded as '%s') is not a valid %s." % (jobtype, name, motherClassName))

    return jobtype


def loadTaskExpander(name):
    return _load(name, TaskExpander)


def loadTaskDecomposer(name):
    return _load(name, TaskDecomposer)


def loadCommandRunner(name):
    return _load(name, CommandRunner)
