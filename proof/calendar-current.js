(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.a359c5550dcd666a.js","sha256":"a359c5550dcd666ab624feda2a41558ff4e3a00bc15eec6224b3b9a9753dd06b","count":2519,"publishedAt":"2026-09-16T17:08:48Z","state":"calendar-state.json","stateSha256":"37898939abbf6343c5c2627b271f2dcbbb73bdbd538850878a87ff0c60d31f74"});
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
