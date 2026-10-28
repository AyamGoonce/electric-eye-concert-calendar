(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.128c16247fa42de4.js","sha256":"128c16247fa42de4cb9524e75eb1a1179993e2d3e0e34ed860a689fcca815199","count":2040,"publishedAt":"2026-10-28T05:53:30Z","state":"calendar-state.json","stateSha256":"42c06f24d2b51b3594796f4c8a6ddb66eb3aa41528ab3d01e667f850192fa437","sourceState":"calendar-source-state.json","sourceStateSha256":"1b1fcceb2284235fefd164838c48fe5b234cc4ca330ac4828e00c844e66301bc"});
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
