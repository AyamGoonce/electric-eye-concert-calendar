(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.c4f701d29e8dc9e1.js","sha256":"c4f701d29e8dc9e1a5460ec151b6074ac99b5f73812c5c95566bb1f862770f40","count":2031,"publishedAt":"2026-11-03T06:57:10Z","state":"calendar-state.json","stateSha256":"34fe081f27f9db87df661cbc99dc4c9369825f4575954423d6fe3d21b1e3fed9","sourceState":"calendar-source-state.json","sourceStateSha256":"b026d7e5aec011d2668972cb0406aa18fe5b43eb60691e8a8916997a5c7d98b6"});
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
