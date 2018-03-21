var args = process.argv.slice(2);
let Parser = require('rss-parser');
let fs = require('fs');
let parser = new Parser({customFields: {
    item: [['media:provincie', 'provincie'],['media:grootste', 'big']]
  }
});


var CSVTextBuffer = "";
var gemeenteResultatenRange = {min:1, max:380}



function isGemeenteUitslag(link){
	tlink = link.split("/")[6].split(".xml")[0];
	return (tlink >= gemeenteResultatenRange.min && tlink <= gemeenteResultatenRange.max);
}

function ParseAMPRSSFeed(feed){
	items = feed.items;
	for (var item in items) {
    if (items.hasOwnProperty(item)) {
        	if(isGemeenteUitslag(items[item].link)){
				let gemeente = items[item];
				let naam = gemeente.title;
				let huidigGrootste = gemeente.big['$'].cur;
				let histGrootste = gemeente.big['$'].prev;
				CSVLine = `${naam},${huidigGrootste},${histGrootste}\n`;
				CSVTextBuffer += CSVLine;
        	}
    	}
	}
	fs.writeFile('results.csv', CSVTextBuffer, 'utf8',() => {
		console.log("Wrote file to results.csv")
	});
}


RSSurl = ""
if(args.length > 0){
  RSSurl = args[0]
} else {
	console.log("Use node csvGenerator.js https://verkiezingsdienst.anp.nl/rss/verkiezingen/gr2014/index.rss");
	process.exit()
}

parser.parseURL(RSSurl, function(err, feed) {
  ParseAMPRSSFeed(feed);
})

