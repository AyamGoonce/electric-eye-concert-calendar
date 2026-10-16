(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.6510c835fd132db6.js","sha256":"6510c835fd132db65fac44ddeab3e64539a4dc811b8c34498d2e5eead1e24529","count":2127,"publishedAt":"2026-10-16T04:41:07Z","state":"calendar-state.json","stateSha256":"bd97b451cae5265f877e067034a6d301468e52a4e456632bbac584ff764e8ecd","sourceState":"calendar-source-state.json","sourceStateSha256":"bdecaabe5ea79a5a5e4466816ac20437c041de8c83d264ae083d3c9b78f302ab"});
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
