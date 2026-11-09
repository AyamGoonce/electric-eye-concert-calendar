(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.3c7416d9448d6936.js","sha256":"3c7416d9448d6936eb95ec31e3274dcd3ee5a737c3e3c1205acc69b779855b61","count":2205,"publishedAt":"2026-11-09T16:38:44Z","state":"calendar-state.json","stateSha256":"ff94f85f12ada4ee3d91663a89042dd8b5877e31d722f10c83e6d805dd56cf73","sourceState":"calendar-source-state.json","sourceStateSha256":"f8726adbe740b8de658f59c2ab0a0811b189c23c74c4acc7ccb83f153799ec54"});
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
