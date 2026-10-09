(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.9077d982ddc801ba.js","sha256":"9077d982ddc801baeff68a34f1df15959e848bf793b1b15c01e51984694fcefc","count":2211,"publishedAt":"2026-10-09T10:43:08Z","state":"calendar-state.json","stateSha256":"ea47ce774a29bf0cdeac33fc43c617eb515b76de40bf329f49689086bd437c50","sourceState":"calendar-source-state.json","sourceStateSha256":"98877f9755bd12f143b3561c8c24ae174b5e5dd8a780d589fd471e690de2027e"});
  var currentSource = document.currentScript && document.currentScript.src;
  window.ElectricEyeConcertManifest = manifest;
  document.dispatchEvent(new CustomEvent("ee:concert-manifest-ready", {detail:manifest}));
  var script = document.createElement("script");
  script.src = new URL(manifest.data, currentSource || window.location.href).href;
  script.onerror = function(){
    document.dispatchEvent(new CustomEvent("ee:concert-data-error", {detail:{reason:"data asset unavailable"}}));
  };
  document.head.appendChild(script);
}());
