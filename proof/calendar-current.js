(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.3e700ab4842497a9.js","sha256":"3e700ab4842497a917af3b2417df1198061843b401a6bcffcab3ca9a90496f5f","count":2479,"publishedAt":"2026-09-03T11:32:28Z","state":"calendar-state.json","stateSha256":"206b58cca00314b9dbb30e556d8f37a2e55d4be9f94b275a172a4773e97e4a62"});
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
