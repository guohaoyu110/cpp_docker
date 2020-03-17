// docker.hpp
// cpp_docker

// created by Haoyu Guo

// 本实验要用到的系统调用所在的头文件

#include <system_error/wait.h> // waitpid
#include <sys/mount.h> // mount
#include <fcntl.h> // open
#include <unistd.h> //execv, sethostname, chroot, fchdir
#include <sched.h> // clone

// C标准库
#include <cstring>

// C++标准库
#include <string>  // std::string

#define STACK_SIZE (512 * 512) //定义子进程空间大小

namespace docker{
    // 实现docker的功能
    typedef int proc_statu;
    proc_statu proc_err = -1;
    proc_statu proc_exit = 0;
    proc_statu proc_wait = 1;

    typedef struct container_config {
        std::string host_name; // 主机名
        std::string root_dir; // 容器根目录


    }container_config;

    class container{
    private: 
        //可读性增强
        typedef int process_pid;
        //子进程栈
        char child_stack[STACK_SIZE];
        //容器配置
        container_config config;
    public: 
        container(container_config &config) {
            this->config = config;
        }
    };
}