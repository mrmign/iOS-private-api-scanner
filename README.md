iOS-private-api-scanner
=======================

scan iOS private api

这里提供的脚本只是针对 应用进行静态扫描，(本着宁可错杀一万，不可漏杀一人的原则)扫描结果准备率比较低，需要进行人工排除。

另一种方案：

就是动态扫描，这个需要应用运行起来才可以，每当调用方法时就判断是否是私有API，但是效率会很低，而且不能保证代码完全覆盖。

有其他想法的人欢迎提出来，大家一起出谋划策。

ps最近苹果好像加强了对私有api的检测。

## License

This code is distributed under the terms and conditions of the GPL v2 license.
