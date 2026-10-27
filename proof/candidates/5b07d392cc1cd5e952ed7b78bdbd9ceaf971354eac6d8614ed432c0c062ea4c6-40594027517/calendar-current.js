(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.5b07d392cc1cd5e9.js","sha256":"5b07d392cc1cd5e952ed7b78bdbd9ceaf971354eac6d8614ed432c0c062ea4c6","count":2060,"publishedAt":"2026-10-27T22:23:07Z","state":"calendar-state.json","stateSha256":"5a8ea5070c6526610a4d9ee57ef389699192899c5ddc26bd7821ff1036be621d","sourceState":"calendar-source-state.json","sourceStateSha256":"d6dbfd173882d9227ec5e7a2a70280c8f6f989473d0c93fabd1e83dfdc44c329"});
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
