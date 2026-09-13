(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.e86307e1f66772a3.js","sha256":"e86307e1f66772a32539b55bdcdd146995068a11c7778ac616a7eff5d49f18e9","count":2437,"publishedAt":"2026-09-13T16:28:30Z","state":"calendar-state.json","stateSha256":"20da961a9a82061e591551dac2c7a59026ab175054f3d0a8c4467e5b0e240235"});
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
