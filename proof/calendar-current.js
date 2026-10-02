(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.2f43c54db6f8dc80.js","sha256":"2f43c54db6f8dc80bf48e69cad3870813e70d2b154371a33e1847b3fcff7d6d8","count":2214,"publishedAt":"2026-10-02T10:02:56Z","state":"calendar-state.json","stateSha256":"a8b0807a86a6439324099c722109745e7bed1fb6d060da801aaf972a8f6950ee","sourceState":"calendar-source-state.json","sourceStateSha256":"c0c7e4901d0dd698f000f47d0af5160bfe9d8848e282bb09835d6c96431176d7"});
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
