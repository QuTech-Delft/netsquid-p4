"""Abstract base class for P4 devices."""

from abc import ABC, abstractmethod
import json

from netsquid.components.component import Component
from netsquid.protocols import Protocol

import netsquid as ns


class P4Device(ABC, Component):
    """Abstract base class for P4 devices. A P4 Device is a NetSquid component.

    Parameters
    ----------
    name : `str`
        The name for this device.
    p4_processor : `~pyp4.processor.Processor`
        The P4 processor loaded with the P4 program.
    port_names : list of `str`, optional
        The names of the ports to add during construction.

    """

    P4_MAX_PORT = 0x1FF

    def __init__(self, name, p4_processor, port_names=None):
        self.__port_protocols = {}
        Component.__init__(self, name, port_names=port_names)
        self.__p4_processor = p4_processor

    @property
    def _p4_processor(self):
        return self.__p4_processor

    def load(self, program_file_name):
        """Load a P4 program onto the device processor.

        Parameters
        ----------
        program_file_name : `str`
            The file name with the P4 program in BM JSON format.

        Returns
        -------
        `netsquid_p4.device.Device`
            For convenience the device itself is returned.

        """
        with open(program_file_name, encoding="utf-8") as program_file:
            program = json.load(program_file)
        process = self._create_process(program)
        self._p4_processor.load(process)
        return self

    def unload(self):
        """Unload the currently running P4 program."""
        self._p4_processor.unload()

    @abstractmethod
    def _create_process(self, program):
        raise NotImplementedError

    def table(self, block, name):
        """Access a table in the P4 processor.

        Parameters
        ----------
        block : `str`
            The name of the block in which the table is defined. Note that the name is defined by
            the architecture, not the program itself. E.g. the ingress block is called "ingress"
            regardless of how that block is called in the program.
        name : `str`
            The name of the table as defined by the program.

        Returns
        -------
        `pyp4.table.Table`
             The table.

        """
        try:
            return self.__p4_processor.table(block, name)
        except ValueError as verr:
            raise ValueError(f"Device {self.name} failed to access table :: {verr}") from verr

    def add_ports(self, names):
        """Add ports to this component.

        Parameters
        ----------
        names : list of `str`
            List of the port names to add.

        Returns
        -------
        `List[~netsquid.components.component.Port]`
            List of the ports with the given names.

        """
        for name in names:
            P4Device.validate_port_name(name)

        # Use superclass to formally add the ports.
        new_ports = super().add_ports(names)

        # Install the protocols on the new ports.
        for port in new_ports:
            self.__port_protocols[port.name] = PortProtocol(self, port).start()

        # Return the ports as that is what the superclass's add_ports does.
        return new_ports

    @staticmethod
    def validate_port_name(port_name):
        """Check whether the given port name is valid for a P4Device.

        Valid port names are positive integers that are less than or equal to
        `netsquid_p4.device.P4Device.P4_MAX_PORT`.

        Parameters
        ----------
        port_name : `str`
            The port name to validate.

        Raises
        ------
        `ValueError`
             If the port name is not valid.

        """
        try:
            port_num = int(port_name, 0)
        except ValueError as error:
            raise ValueError(
                f"{port_name} is not an integer (P4Device ports must be integers)"
            ) from error
        if port_num > P4Device.P4_MAX_PORT:
            raise ValueError(
                f"{port_name} is greater than the maximum allowed value ({P4Device.P4_MAX_PORT})"
            )

    @abstractmethod
    def cnetwork_process(self, port_name, packet):
        """Process an incoming classical network packet.

        Parameters
        ----------
        port_name : `str`
            The name of the port the packet arrived on. Must be convertible to an `int`.
        packet : `~pyp4.packet.HeaderStack`
            The incoming packet.

        """
        raise NotImplementedError

    def _cnetwork_execute(self, port_name, packet):
        """Send out a classical network packet generated by the P4 processor.

        Parameters
        ----------
        port_name : `str`
            The name of the egress port.
        packet : `~pyp4.packet.HeaderStack`
            Outgoing packet.

        """
        self.ports[port_name].tx_output(packet)


class PortProtocol(Protocol):
    """Listen for incoming packets, hand off to the P4 processor.

    Parameters
    ----------
    device : `netsquid_p4.device.P4Device`
        The device on which this protocol is running.
    port : `~netsquid.components.component.Port`
        The port to listen on.

    """

    def __init__(self, device, port):
        super().__init__(f"{device.name}-{port.name}")
        self.__device = device
        self.__port = port

    def run(self):
        """Run the protocol."""
        while True:
            yield self.await_port_input(self.__port)
            for packet_in in self.__port.rx_input().items:
                self.__device.cnetwork_process(self.__port.name, packet_in)


class NetsquidRuntime:
    """Base class for simulated runtimes in NetSquid.

    Parameters
    ----------
    magnitude : `float`, optional
        Time magnitude to use. Default is nanoseconds.
    """

    def __init__(self, magnitude=ns.NANOSECOND):
        super().__init__()
        self.__magnitude = magnitude
        self.__start_time = ns.sim_time(magnitude)

    def time(self):
        """Get the simulated time.

        Returns
        -------
        `int`
            The current time on the device. The clock must be set to 0 every time the switch starts.

        """
        return ns.sim_time(self.__magnitude) - self.__start_time