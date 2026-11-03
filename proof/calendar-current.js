(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.eefb67269937de7f.js","sha256":"eefb67269937de7fd63a8b603dc68c7e1ad356b32a2c04b2f10896c0485a625e","count":2038,"publishedAt":"2026-11-03T10:37:28Z","state":"calendar-state.json","stateSha256":"01cd1b0a9812e107cb34a494a84e17c29a85b1e3d88c0c344f992e4ed2e57a6d","sourceState":"calendar-source-state.json","sourceStateSha256":"d0be4dda69a1b7ab54e54e4f2fe7d844826a919ebe7a29634e5293e4d5dd4146"});
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
