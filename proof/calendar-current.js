(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.f2ef8f883b0a3f07.js","sha256":"f2ef8f883b0a3f070705b306e64e6ee24120fb03006502d32b51dec5cadcdf27","count":1851,"publishedAt":"2026-08-27T22:24:58Z","state":"calendar-state.json","stateSha256":"a81359ae8725cc893fd7e7611d7dbfef60f53624a8a88a493b135c36fd810064"});
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
