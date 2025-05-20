# 这里是使用Vue3、SpringBoot3、Docker(Dockerfile、docker-compose)做的简单的Docker镜像制作部署，是一个demo级的项目，可供一些初学者在学习一段时间后简单的了解和熟悉简单的Docker基础

## 后端SpringBoot3
- 后端是使用SpringBoot3搭建的后端，主要功能是实现根据数据库中的用户id查询用户相关信息
- 相关详情可见data、frontend

## 前端Vue3
- 前端是使用Vue3简单搭建了一个简陋的用户查询页面，主体主要是一个很小的查询窗口，包括一个输入框和一个按钮以及查询后的显示区域

## 数据库
- 数据库使用的是MySQL8.4.4，值得注意的是，如果要更改数据库版本的使用，整个后端的MySQL连接驱动依赖需要相关的修改，因为Java本身以及SpringBoot3对每一个版本的适配很是挑剔
- 数据库的初始化脚本在user.sql里，整体数据库结构是：user-user

## Docker
- Docker镜像的环境部署，主要涉及Dockerfile、docker-compoe工具及yml文件的使用和编写
- 由于前后端分别需要不同的运行环境，因此会涉及到JDK等环境的安装，具体详情可查看Dockerfile以及docker-compoes.yml
