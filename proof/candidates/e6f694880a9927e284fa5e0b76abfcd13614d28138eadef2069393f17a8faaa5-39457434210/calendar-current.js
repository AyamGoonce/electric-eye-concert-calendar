(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.e6f694880a9927e2.js","sha256":"e6f694880a9927e284fa5e0b76abfcd13614d28138eadef2069393f17a8faaa5","count":2082,"publishedAt":"2026-10-20T16:29:01Z","state":"calendar-state.json","stateSha256":"4e4362b7728f0aadfd43c9d76ec6411bbc6dc4810a97527070bdd2554d2e0d37","sourceState":"calendar-source-state.json","sourceStateSha256":"3e39c91ee9f28f720fd1f602129ec89315f390b23a69916d30cbeae86116108f"});
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
