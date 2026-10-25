(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.fa9a2afabb25ab4a.js","sha256":"fa9a2afabb25ab4a46105ae6dde3186a3e24f655c8cfd958d91b7ba44a72f5c1","count":2049,"publishedAt":"2026-10-25T23:20:30Z","state":"calendar-state.json","stateSha256":"9decae2afdd93ed8c378513b3c7a62c3f6dd0e686714f8c80714933de18c608e","sourceState":"calendar-source-state.json","sourceStateSha256":"b903210b006fda68d8b046aa3ce178bc5f0a94738617cf7d53279b9b736f2463"});
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
