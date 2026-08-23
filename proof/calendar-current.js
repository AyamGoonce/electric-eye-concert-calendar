(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.7b7c3a487d7afb99.js","sha256":"7b7c3a487d7afb99ca7f33810cb827d9eea8ea4ebbc846b4bf2939b94d924a02","count":1709,"publishedAt":"2026-08-23T11:03:00Z","state":"calendar-state.json","stateSha256":"a7cedd383bc03351e3a13997de2a8a5432b63e185415b5f442a3d1887e59e47a"});
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
