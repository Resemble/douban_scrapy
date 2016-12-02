/**
 * Created by ranran on 2016/10/17.
 */

// // 页面加载
// var page = require('webpage').create();
// page.open('http://cuiqingcai.com', function(status){
//     console.log("Status:" + status);
//     if(status === "success"){
//         page.render('example.png');
//     }
//     phantom.exit();
// })

// // 测试页面加载速度
// var page = require('webpage').create(),
//     system = require('system'),
//     t, address;
//
// if(system.args.length === 1){
//     console.log('Usage: loadspeed.js <some URL>');
//     phantom.exit();
// }
//
// t = Date.now();
// address = system.args[1];
// page.open(address, function(status){
//     if(status !== 'success'){
//         console.log('FATL to load the address');
//     }else{
//         t = Date.now() -t;
//         console.log('Loading' + system.args[1]);
//         console.log('Loading time' + t + 'msec');
//     }
//     phantom.exit();
// });

// // 代码评估
// var url = 'http://www.baidu.com'
// var page = require('webpage').create();
// page.open(url, function(status){
//     var title = page.evaluate(function(){
//         return document.title;
//     });
//     console.log('Page title is ' + title);
//     console.log('中国');
//     phantom.eixt();
// });

// // 重写onConsoleMessage()
// var url = 'http://www.baidu.com'
// var page = require('webpage').create();
// page.onConsoleMessage = function(msg){
//     console.log(msg);
// };
// page.open(url, function(status){
//     page.evalute(function(){
//         console.log(document.title);
//     });
//     phantom.eixt();
// });

// // 屏幕捕获
// var page = require('webpage').create();
// page.open('http://github.com/', function(){
//     page.render('github.png');
//     phantom.exit();
// })

// // viewportSize和clipRect
// var page = require('webpage').create();
// page.viewportSize = {width: 1024, height: 768};
// page.clipRect = {top: 0, left: 0, width: 1024, height: 768};
// page.open('http://cuiqingcai.com/', function(){
//     page.render('germy.png');
//     phantom.exit();
// })

// // 网络监听
// var url = 'http://www.cuiqingcai.com';
// var page = require('webpage').create();
// page.onResourceRequested = function(request){
//     console.log('Request' + JSON.stringify(request, undefined, 4));
// };
// page.onResourceReceived = function(response){
//     console.log('Receive' + JSON.stringify(response, undefined, 4));
// };
// page.open(url);

// // 页面自动化处理
// var page = require('webpage').create();
// console.log('The default user agent is' + page.settings.userAgent);
// page.settings.userAgent = 'SpecialAgent';
// page.open('http://www.httpuseragent.org', function(status){
//     if(status !== 'success'){
//         console.log('Unable to access network');
//     }else{
//         var ua = page.evaluate(function () {
//             return document.getElementById('myagent').textContent;
//         });
//         console.log(ua);
//     }
//     phantom.exit();
// });

// 使用附加库
var page = require('webpage').create();
page.open('http://www.sample.com', function(){
    page.includes("http://ajax.googleapis.com/ajax/libs/jquery/1.6.1/jquery.min.js", function(){
        page.evalute(function(){
            $("button").click();
        });
        phantom.exit();
    });
});
