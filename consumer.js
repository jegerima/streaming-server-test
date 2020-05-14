const express = require('express');

const app = express();

app.set('view engine', 'pug');

app.get('/', function(req, res){
	res.render('flv');
});

app.get('*', function(req,res){
	res.send('<h4>404</h4>');
});

app.listen(8051);


// https://stackoverflow.com/questions/31742851/remove-progress-bar-from-html5-video-player-in-full-screen
// https://video.stackexchange.com/questions/12905/repeat-loop-input-video-with-ffmpeg