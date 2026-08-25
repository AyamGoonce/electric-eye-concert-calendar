(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.725746bd88217ef7.js","sha256":"725746bd88217ef7cb73a560f25af55ec6461c95fe820babb184ed4f11f763a9","count":1739,"publishedAt":"2026-08-25T13:22:04Z","state":"calendar-state.json","stateSha256":"f32f30c393536f62fa1471fbe743d81740ea64166e604843499fbf3fef5ea19e"});
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
