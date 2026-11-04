(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.647c43e42e91e29e.js","sha256":"647c43e42e91e29e64b8844a01382985eff8667595a606b9c4c9ea7493828650","count":2036,"publishedAt":"2026-11-04T06:38:26Z","state":"calendar-state.json","stateSha256":"f3d4795ac152cf2353165e75ea8ac02f543c9f9ba316033487b8cf3f191b2325","sourceState":"calendar-source-state.json","sourceStateSha256":"4a4971259532752433ba112780c2eedff6c0c50f88d8ae57c1f22005fc9e3de4"});
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
