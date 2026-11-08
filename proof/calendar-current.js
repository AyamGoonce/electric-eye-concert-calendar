(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.3dba616488369cd8.js","sha256":"3dba616488369cd845623f8c3118941248123d5e91bb3663ba7ff068188116c1","count":1981,"publishedAt":"2026-11-08T10:32:13Z","state":"calendar-state.json","stateSha256":"df715f9e6388bc6e41ac8e4aa5a908c372344d2d1ca789b2d4208e71cc40e651","sourceState":"calendar-source-state.json","sourceStateSha256":"14d0a287002b6417433db8c0712d5a50a0716a53920e615803838b4e6d702267"});
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
