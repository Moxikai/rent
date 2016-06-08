/**
 * Created by guangtouling on 16/6/7.
 */
var casper = require('casper').create();
//获取参数
var url = casper.cli.args[0];

casper.start(url,function(){
    this.echo(this.getHTML());
    this.capture('test.png');
});

casper.run();