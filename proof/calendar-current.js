(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.4bce51c10ff78f99.js","sha256":"4bce51c10ff78f999923b22ae52f50fb60d9f1bcf290b7e94324e611b4cbe0cb","count":2035,"publishedAt":"2026-10-27T00:33:42Z","state":"calendar-state.json","stateSha256":"d4dce9804d5e81eafeca3d17ed99987b1ff4adaca993efb2a8bfac9019378793","sourceState":"calendar-source-state.json","sourceStateSha256":"655733f93a51562e365780bf1f12cd00b915189b8e965dc51a4f7e3de0e58b82"});
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
