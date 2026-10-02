(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.bcb5c7653fca6573.js","sha256":"bcb5c7653fca65739848dc005dd4ddc5c7b2d3ed3ca194a65096e984fd65f64a","count":2207,"publishedAt":"2026-10-02T00:51:16Z","state":"calendar-state.json","stateSha256":"e369db4fa3bf2dcc299cb66883e77b03b703aebf15396318dee7123a1daea7c5","sourceState":"calendar-source-state.json","sourceStateSha256":"4804d838c24c8e70db584be992599c859ff74a4dc6d5993445193800b0a0818e"});
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
