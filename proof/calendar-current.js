(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.78c814ae4011b479.js","sha256":"78c814ae4011b479b0224efb6b5411264c7316d9a53c89735c882ebbd678dee9","count":2484,"publishedAt":"2026-09-11T11:33:15Z","state":"calendar-state.json","stateSha256":"af56ed2d7c1fb8e8783f8e39ef7a7ec732fd4c3f9624d76faaf43da41ca188c8"});
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
