(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.a88979bc8e8f483e.js","sha256":"a88979bc8e8f483e56d987f686bf42bc9917e4e052037989bbc63d96895766af","count":2478,"publishedAt":"2026-09-07T17:35:44Z","state":"calendar-state.json","stateSha256":"9e6c280fa3b7bffc3098b722ee788848c1cbe8b40fad36d57a349a65ce0cac5c"});
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
