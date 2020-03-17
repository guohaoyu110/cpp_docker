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
        // 将STDIN 绑定到容易的 /bin/bash 中，所以我们可以给docker::container 类编写一个start_bash()
        void start_bash(){
            // 将C++ std::string 安全的转换为C 风格的字符串char *
            std::string bash = "/bin/bash";
            char *c_bash = new char[bash.length()+1]; // +1 用于存放 '\0'
            strcpy(c_bash, bash.c_str());
            char* const child_args[] = { c_bash, NULL};
            execv(child_args[0], child_args); // 在子进程中执行 /bin/bash
            delete []c_bash;
        }
    public: 
        container(container_config &config) {
            this->config = config;
        }

        void start(){
            // 如果不用lambda表达式，但这时必须在类中定义一个静态的成员函数，这会使得代码很不美观。
            auto setup = [](void *args) -> int {
                auto _this = reinterpret_cast<container*>(args);

                // 对容器进行相关配置
                // ...
                return proc_wait;
            };
            process_pid child_pid = clone(setup, child_stack+STACK_SIZE, SIGCHLD, this);// 子进程退出时会发出信号给父进程
            //移动到栈底
            waitpid(child_pid, nullptr, 0); //等待子进程的退出
        }
        // docker::container::start()这个方法使用了clone这个Linux系统调用，同时，为了让我们的回调函数setup顺利活的我们的docker::container
        // 实例对象，可以通过clone()中的第四个参数进行传递，这里，我们传递了this指针
        // 而对于 setup 而言，我们使用了 lambda 表达式创建 setup 这个回调函数。 
        // 在 C++ 中，捕获列表为空的 lambda 表达式能够作为函数指针进行传递。因此，setup 也就成为了传递给 clone() 的回调函数。


    };
}