// 
// main.cpp
// created by Haoyu Guo

#include "docker.hpp"
#include <iostream>

int main(int argc, char** argv){
    std::cout << "...start container"<< std::endl;
    docker::container_config config;

    // 配置容易
    // ....

    docker::container container(config);
    container.start();
    std::cout<< "stop container..." << std::endl;
    return 0;
}