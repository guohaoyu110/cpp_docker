# cpp_docker
Use C++ to implement a naive docker, I implement the following functions:

- [x] Independent file system

- [x] Network access support

- [x] Limitation of container resources

## Namespace
What's the difference between "namespace" mean in C++, Linux and Docker?

* In C++, each namespace isolates the same name for different parts. As long as the names of namespaces are different, the function name in the namespace can be the same, thereby solving the problem of function name conflicts.

* Linux namespace is a technique provided by Linux kernel, it provides a resource isolation solution for applications in Linux, which may seem similar to that in C++. We know that system resources such as PIC, IPC and network should be managed by the operating system itself. But the Linux namespace can make these resources not appear globally and some of them belong to a specific namespace.

* In Docker technique, we often hear the terms LXC and system-level virtualization. LXC uses the technique of Namespace to achieve resource isolation before different containers. With Namespace technique, processes in different containers belong to different Namespaces and do not interfere with each other. In general, Namespace provides a lightweight form of virtualization, allowing us to run system global properties.

