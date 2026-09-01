(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.a65690aef226d590.js","sha256":"a65690aef226d590cf56ba094a85c30a57d697f6f10f2e85a7c4c2c51f449622","count":2234,"publishedAt":"2026-09-01T21:13:40Z","state":"calendar-state.json","stateSha256":"10066419a83ab649d8710fbf0dbd00e4a47c5719223762f7bdf3ed2750cebfee"});
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
