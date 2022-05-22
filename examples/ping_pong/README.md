# Ping Pong example

This example illustrates the basic soft switch.

## Topology

```
 ------                         --------
|      |                       |        |
| host | ----- Classical ----- | switch |
|      |                       |        |
 ------                         --------
```

Both nodes use port `0x0` for the connection.

## Instructions

Run this example from the top-level directory:
```
python3 -m examples.ping_pong.run
```

This will load the program from [`p4/ping-pong.json`](p4/ping-pong.json) which was compiled from
[`p4/ping-pong.p4`](p4/ping-pong.p4) onto the switch. The host does not run a P4 program.

## What you will see

A packet with a TTL header initialised to 10 is sent from `host` to `switch`. The switch will keep
decrementing the TTL and returning the packet until the TTL is decremented to 0 at which point it
will drop it.
