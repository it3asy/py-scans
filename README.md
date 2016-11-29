# 关于
常常需要对批量目标进行处理，像网站目录扫描、端口扫描、漏洞探测等……整理一些脚本放在这里：  

* scandirs.py  
    探测网站指定目录是否存在。  
    
* scanports.py  
    探测主机指定端口是否开放。  
    
* scanuris.py  
    探测网站路径状态，用于判断指定路径是否存在，类似于wscan。


# 场景

1. 批量网站快速查找WebLogic控制台  
    python scandirs.py --targets=targets.txt --dir=console --go

2. 批量网站中快速查找编辑器  
    python scandirs.py --targets=targets.txt --dict=dicts/editors.txt --go  
    python scandirs.py --targets=targets.txt --dict=dicts/fckeditor.txt --nogreedy --recursive --go

3. 批量网站快速查找WebService  
    python scanuris.py --targets=targets.txt --dict=dicts/webservices.txt --status=200 --content "wsdl" --go

4. 批量IP地址中探测查找HTTP服务  
    python scanports.py --targets=targets.txt --port=80-90,443,8080-8090 --go
