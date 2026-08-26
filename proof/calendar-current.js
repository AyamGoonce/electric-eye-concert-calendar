(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.c3ef29aa40cef6d8.js","sha256":"c3ef29aa40cef6d863c4206e1a1ca1b60d25afe813ea9e5123927f1a57f8c884","count":1712,"publishedAt":"2026-08-26T02:06:05Z","state":"calendar-state.json","stateSha256":"bb1c82453a8160c7dcc07ee18b52ae161857dbecd394498699d0f00d835ac2b6"});
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
