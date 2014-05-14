主线程               |      逻辑线程                    |    执行线程              |    通信/处理函数


                     
                     
pp_main -------------|	
[主线程负责初始化]   |
                     |--- pp_dama ----------------------|--------------------------|
                     |   [打码线程,一个tcp server]                                 |
                     |                                                             |--- proc_dama
                     |
                     |
                     |--- pp_control--------------------|--------------------------|
                     |   [控制线程,一个tcp server]                                 |
                     |                                                             |
                     |                                                             |--- proc_control
                     |
                     |
                     |--- pp_client(x3) ----------------|
                         [投标线程]                     |
                                                        |--- client_login ---------|
                                                        |   [子线程]               |
                                                        |                          |--- proc_login
                                                        |                          |
                                                        |                          |
                                                        |                          |--- proc_login_udp
                                                        |                          |
                                                        |                          |
                                                        |                          |--- proc_status_udp
                                                        |
                                                        |
                                                        |--- client_image ---------|
                                                        |   [子线程]               |
                                                        |                          |--- proc_image
                                                        |                          |
                                                        |                          |
                                                        |                          |--- proc_image_decode
                                                        |
                                                        |
                                                        |--- client_price ---------|
                                                            [子线程]               |
                                                                                   |--- proc_price




pp_test -------------|----------------------------------|--------------------------|
                                                                                   |
                                                                                   |--- test_udp
                                                                                   |
                                                                                   |
                                                                                   |--- test_login
                                                                                   |   
                                                                                   |
                                                                                   |--- test_image (保存jpg到文件)
                                                                                   |   
                                                                                   |   
                                                                                   |--- test_price




dm_proto ------------|----------------------------------|--------------------------|--- proto_dama ---------------------|
                                                                                                                        |   
                                                                                                                        |--- make_decode_req
                                                                                                                        |   
                                                                                                                        |   
                                                                                                                        |--- parse_decode_ack





ct_proto ------------|----------------------------------|--------------------------|--- proto_ct -----------------------|
                                                                                                                        |   
                                                                                                                        |--- make_ack  (login, image_warmup(3), image_shoot(3), price_warmup(3), price_shoot(3)) 
                                                                                                                        |   
                                                                                                                        |   
                                                                                                                        |--- parse_req (login, image_warmup(3), image_shoot(3), price_warmup(3), price_shoot(3))  



pp_proto ------------|----------------------------------|--------------------------|
                                                                                   |   
                                                                                   |--- proto_udp ----------------------|
                                                                                   |                                    |
                                                                                   |                                    |--- make_format
                                                                                   |                                    |
                                                                                   |                                    |
                                                                                   |                                    |--- make_client
                                                                                   |                                    |
                                                                                   |                                    |
                                                                                   |                                    |--- make_logoff
                                                                                   |                                    |
                                                                                   |                                    |
                                                                                   |                                    |--- parse_info
                                                                                   |                                    |
                                                                                   |                                    |
                                                                                   |                                    |--- parse_format 
                                                                                   |                                    |
                                                                                   |                                    |
                                                                                   |                                    |--- parse_msg
                                                                                   |                                    |
                                                                                   |                                    |
                                                                                   |                                    |--- parse_relogin
                                                                                   |                                    |
                                                                                   |                                    |
                                                                                   |                                    |--- parse_addserv
                                                                                   |                                    |
                                                                                   |                                    |
                                                                                   |                                    |--- parse_marquee
                                                                                   |                                    
                                                                                   |   
                                                                                   |--- proto_login --------------------|
                                                                                   |                                    |  
                                                                                   |                                    |--- make_login  
                                                                                   |                                    |  
                                                                                   |                                    |  
                                                                                   |                                    |--- parse_login  
                                                                                   |   
                                                                                   |   
                                                                                   |--- proto_image --------------------|
                                                                                   |                                    |  
                                                                                   |                                    |--- make_image  
                                                                                   |                                    |  
                                                                                   |                                    |  
                                                                                   |                                    |--- parse_image  
                                                                                   |   
                                                                                   |   
                                                                                   |--- proto_price --------------------|
                                                                                                                        |  
                                                                                                                        |--- make_price  
                                                                                                                        |  
                                                                                                                        |  
                                                                                                                        |--- parse_price  
                                                                                                                          


//==================================================================================================================================================================================================================
                                                                                                     
                                                                 
              |--- ppthread_trigger --|---------------------|----------------------|--- proc_trigger(处理触发信号的相关事宜)
              |  [程序初始化后启动]                                                
              |  [子线程销毁后销毁]                                                
              |  [只有一个线程]                                                                                                
              |                                             |----------------------|--- proc_login(SSL登录)
              |                                             |                                         
              |                                             |                                         
              |                                             |----------------------|--- proc_login_udp(UDP登录)
              |                                             |                                         
              |                                             |                                         
              |                       |--- ppthread_login --|----------------------|--- proc_status_udp(监控UDP里的状态变化)
              |                       |[client线程启动后启动]                                                              
              |                       | [投标完成后销毁]                                                              
              |                       |                                                             
pp_control ---|--- ppthread_client ---|--- ppthread_bid0 ---|----------------------|--- proc_image(立即执行)
                [程序初始化后启动]    | [上半场开始后启动]                         |                  
                [子线程销毁后销毁]    | [投标完成后销毁]                           |                  
                [每个投标号一个线程]  |                                            |--- proc_image_decode(短连接,阻塞等待返回)
                                      |                                            |                
                                      |                                            |               
                                      |                                            |--- proc_price(立即执行)
                                      |                                                             
                                      |                                                             
                                      |--- ppthread_bid1 ---|--- ppthread_image1 --|--- proc_image(先预热连接，等事件信号执行)
                                      | [下半场开始后启动]  | [下半场结束后销毁]   |                   
                                      | [下半场结束后销毁]  |                      |                                        
                                      |                     |                      |--- proc_image_decode(短连接,阻塞等待返回)
                                      |                     |                                                               
                                      |                     |                                                               
                                      |                     |--- ppthread_price1 --|--- proc_price(先预热连接，等事件信号执行)
                                      |                       [下半场结束后销毁]                            
                                      |                                                             
                                      |--- ppthread_bid2 ---|--- ppthread_image2 --|--- proc_image(先预热连接，等事件信号执行)
                                        [下半场开始后启动]  | [下半场结束后销毁]   |                   
                                        [下半场结束后销毁]  |                      |                                        
                                                            |                      |--- proc_image_decode(短连接,阻塞等待返回)
                                                            |                                                               
                                                            |                                                               
                                                            |--- ppthread_price2 --|--- proc_price(先预热连接，等事件信号执行)
                                                              [下半场结束后销毁]                            
                                                               
                                                               
                                      |---------------------|                         
                                      | bid1和bid2两个线程  |
                                      | 采用不同的投标策略  |                                                           
                                      | bid1由时间触发      |
                                      | bid2由价格触发      |
                                      |---------------------|                         
