(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.ea531803fb63d582.js","sha256":"ea531803fb63d58243cb79e92d70d3cbef5e35f2052dcf7e81ff007ce7155b1e","count":2224,"publishedAt":"2026-10-02T17:54:23Z","state":"calendar-state.json","stateSha256":"54fca5daf2ee0bf3a5ad15c4f7f419fee8962f3f0e25b001f84ba8e222e30dd3","sourceState":"calendar-source-state.json","sourceStateSha256":"38c96d41b8ff18cbb2a72f0c5d8eb410ead56c88546adf7fc22beacdf262a596"});
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
