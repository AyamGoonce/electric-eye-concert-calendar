(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.24dd5b468c590172.js","sha256":"24dd5b468c59017267b04c93de1a9f060553498adaf19006a7f5ee886db179fc","count":2069,"publishedAt":"2026-09-28T12:26:05Z","state":"calendar-state.json","stateSha256":"17dac191d545dca1f1e97c683dc27e3f6919de7455c0f6c32e16e1aa95ec01a8","sourceState":"calendar-source-state.json","sourceStateSha256":"2dbaa979ea1ef8c0e3ac7bcdc2ee5d4298dcd3848912d5baa53736291f5c5a4e"});
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
