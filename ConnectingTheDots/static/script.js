$(document).ready(function() {
    var socket = io.connect('http://127.0.0.1:5000');

    var socket_messages = io('http://127.0.0.1:5000/messages');

    $('#send').on('click', function() {
        var message = $('#message').val();

        socket_messages.emit('message from user', message);

    });

    socket_messages.on('from flask', function(msg) {
        alert(msg);
    });

    socket_messages.on('connect', function() {
        var User = document.getElementById("sentUsername").innerHTML;
        socket.emit('connected', User);
    });

    socket.on('server orginated', function(msg) {
        alert(msg);
    });

    var private_socket = io('http://127.0.0.1:5000/private');

    $('#send_username').on('click', function() {
        private_socket.emit('username', $('#username').val());
    });

    $('#send_private_message').on('click', function() {
        var recipient = $('#send_to_username').val();
        var message_to_send = $('#private_message').val();
        var sentUser = document.getElementById("sentUsername").innerHTML;
        private_socket.emit('private_message', {'username' : recipient, 'message' : message_to_send, 'sentname' : sentUser});
        document.getElementById('private_message').value = "";
    });

    private_socket.on('new_private_message', function(username) {
       alert(username);
       location.reload();
    });

});
var dateFormat = function() {
     var token = /d{1,4}|m{1,4}|yy(?:yy)?|([HhMsTt])\1?|[LloSZ]|"[^"]*"|'[^']*'/g,
         timezone = /\b(?:[PMCEA][SDP]T|(?:Pacific|Mountain|Central|Eastern|Atlantic) (?:Standard|Daylight|Prevailing) Time|(?:GMT|UTC)(?:[-+]\d{4})?)\b/g,
         timezoneClip = /[^-+\dA-Z]/g,
         pad = function(val, len) {
             val = String(val);
             len = len || 2;
             while (val.length < len) val = "0" + val;
             return val;
         };

     // Regexes and supporting functions are cached through closure
     return function(date, mask, utc) {
         var dF = dateFormat;

         // You can't provide utc if you skip other args (use the "UTC:" mask prefix)
         if (arguments.length == 1 && Object.prototype.toString.call(date) == "[object String]" && !/\d/.test(date)) {
             mask = date;
             date = undefined;
         }

         // Passing date through Date applies Date.parse, if necessary
         date = date ? new Date(date) : new Date;
         if (isNaN(date)) throw SyntaxError("invalid date");

         mask = String(dF.masks[mask] || mask || dF.masks["default"]);

         // Allow setting the utc argument via the mask
         if (mask.slice(0, 4) == "UTC:") {
             mask = mask.slice(4);
             utc = true;
         }

         var _ = utc ? "getUTC" : "get",
             d = date[_ + "Date"](),
             D = date[_ + "Day"](),
             m = date[_ + "Month"](),
             y = date[_ + "FullYear"](),
             H = date[_ + "Hours"](),
             M = date[_ + "Minutes"](),
             s = date[_ + "Seconds"](),
             L = date[_ + "Milliseconds"](),
             o = utc ? 0 : date.getTimezoneOffset(),
             flags = {
                 d: d,
                 dd: pad(d),
                 ddd: dF.i18n.dayNames[D],
                 dddd: dF.i18n.dayNames[D + 7],
                 m: m + 1,
                 mm: pad(m + 1),
                 mmm: dF.i18n.monthNames[m],
                 mmmm: dF.i18n.monthNames[m + 12],
                 yy: String(y).slice(2),
                 yyyy: y,
                 h: H % 12 || 12,
                 hh: pad(H % 12 || 12),
                 H: H,
                 HH: pad(H),
                 M: M,
                 MM: pad(M),
                 s: s,
                 ss: pad(s),
                 l: pad(L, 3),
                 L: pad(L > 99 ? Math.round(L / 10) : L),
                 t: H < 12 ? "a" : "p",
                 tt: H < 12 ? "am" : "pm",
                 T: H < 12 ? "A" : "P",
                 TT: H < 12 ? "AM" : "PM",
                 Z: utc ? "UTC" : (String(date).match(timezone) || [""]).pop().replace(timezoneClip, ""),
                 o: (o > 0 ? "-" : "+") + pad(Math.floor(Math.abs(o) / 60) * 100 + Math.abs(o) % 60, 4),
                 S: ["th", "st", "nd", "rd"][d % 10 > 3 ? 0 : (d % 100 - d % 10 != 10) * d % 10]
             };

         return mask.replace(token, function($0) {
             return $0 in flags ? flags[$0] : $0.slice(1, $0.length - 1);
         });
     };
 }();

 // Some common format strings
 dateFormat.masks = {
     "default": "ddd mmm dd yyyy HH:MM:ss",
     shortDate: "m/d/yy",
     mediumDate: "mmm d, yyyy",
     longDate: "mmmm d, yyyy",
     fullDate: "dddd, mmmm d, yyyy",
     shortTime: "h:MM TT",
     mediumTime: "h:MM:ss TT",
     longTime: "h:MM:ss TT Z",
     isoDate: "yyyy-mm-dd",
     isoTime: "HH:MM:ss",
     isoDateTime: "yyyy-mm-dd'T'HH:MM:ss",
     isoUtcDateTime: "UTC:yyyy-mm-dd'T'HH:MM:ss'Z'"
 };

 // Internationalization strings
 dateFormat.i18n = {
     dayNames: [
         "Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat",
         "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"
     ],
     monthNames: [
         "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
         "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"
     ]
 };

 // For convenience...
 Date.prototype.format = function(mask, utc) {
     return dateFormat(this, mask, utc);
 };
        function loadScroll(){
            window.scrollTo(0,document.body.scrollHeight);
            document.getElementById('send_to_username').value = document.getElementById('curChat').innerHTML;
            console.log(document.getElementById('curChat').innerHTML);
        }

        document.getElementById("send_private_message").addEventListener("click", function(){
            var parent = document.getElementById('chatContent');
            var buffer = document.getElementById('buffer'); 
            var newGroup = document.createElement("div"); 
            var details = document.createElement("div");
            var message = document.createElement("div");

            var para = document.createElement("p");
            var para1 = document.createElement("p");
            var para2 = document.createElement("p");

            newGroup.setAttribute("id", "messageContentSent"); 
            details.setAttribute("id", "messageDetails");
            message.setAttribute("id", "chat");

            var chatContent = document.getElementById('private_message').value;
            var node = document.createTextNode(chatContent);
            para.appendChild(node);
            message.appendChild(para);

            var username = document.getElementById('sentUsername').innerHTML;
            var userNode = document.createTextNode(username);
            var timestamp = new Date().format("yyyy-mm-dd hh:MM:ss");
            var timeNode = document.createTextNode(timestamp);
            para1.appendChild(userNode);
            para2.appendChild(timeNode);
            details.appendChild(para1);
            details.appendChild(para2);

            newGroup.appendChild(details);
            newGroup.appendChild(message);
            parent.insertBefore(newGroup, buffer);
            loadScroll();
        }); 

        function addElement(){
            var newDiv = document.createElement("div"); 
            // and give it some content 
            var textContent = document.getElementById('private_message').value;
            var newContent = document.createTextNode(textContent); 
            // add the text node to the newly created div
            newDiv.appendChild(newContent);  
            // add the newly created element and its content into the DOM 
            var currentDiv = document.getElementById("buffer"); 
            document.body.insertBefore(newDiv, currentDiv);
            document.getElementById('chatContent').appendChild(newDiv);
            alert("did this");
        }

        function changeChat(value){
            var text = value.getElementsByTagName('p')[0].innerHTML;
            document.getElementById('curChat').innerHTML = text;
            document.getElementById('send_to_username').value = text;
            window.open('/dashboard/'+document.getElementById('curChat').innerHTML, "_self");
        }