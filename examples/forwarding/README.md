# Forwarding example

This example illustrates a more complicated P4 switching scenario.

## Topology

![topology](https://raw.githubusercontent.com/p4lang/tutorials/76a9067deaf35cd399ed965aa19997776f72ec55/exercises/basic/pod-topo/pod-topo.png)

Image taken from
[p4lang/tutorials](https://github.com/p4lang/tutorials/tree/76a9067deaf35cd399ed965aa19997776f72ec55/exercises/basic)

## Instructions

Run this example from the top-level directory:
```
python3 -m examples.forwarding.run
```

This will load the program from [`p4/forwarding.json`](p4/forwarding.json) which was compiled from
[`p4/forwarding.p4`](p4/forwarding.p4) on the `s*` switches. The end hosts `h*` do not have any P4
program loaded.

## What you will see

In the example `h1` will ping `h2`, `h3`, and `h4`. You will see `h2`, `h3`, and `h4` receiving the
ping and `h1` receiving a response from each. The change in TTL indicates how many intermediate
nodes the packet was switched through.
