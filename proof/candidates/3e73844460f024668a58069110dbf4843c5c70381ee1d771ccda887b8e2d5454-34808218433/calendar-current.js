(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.3e73844460f02466.js","sha256":"3e73844460f024668a58069110dbf4843c5c70381ee1d771ccda887b8e2d5454","count":2430,"publishedAt":"2026-09-14T05:07:35Z","state":"calendar-state.json","stateSha256":"2f83b7ba6d7b815d8b9d96024d7b0cf2ee189a4e500be71a8e17ae4fb5a46978"});
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
