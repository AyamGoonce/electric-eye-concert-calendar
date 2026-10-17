(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.1f016c5d73932e70.js","sha256":"1f016c5d73932e703d16c186c8fe4a39cbf318e3c00bec3480b99e119327c88f","count":2103,"publishedAt":"2026-10-17T15:42:55Z","state":"calendar-state.json","stateSha256":"2e2777d9b8c62ff813ab82a091c56262cc8784e4c35d1d5a7279cd3f1d3c7c70","sourceState":"calendar-source-state.json","sourceStateSha256":"2b5379a143cad86ae18a23f6b415ca86a07dce5b5e9ec4a9b3346b5fb986f87c"});
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
