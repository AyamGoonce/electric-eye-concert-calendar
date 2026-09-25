(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.e713152d65582ed1.js","sha256":"e713152d65582ed11e66ee9cab189d44a61aa216c2dd8df7f60cda6081cc9514","count":2124,"publishedAt":"2026-09-25T15:57:55Z","state":"calendar-state.json","stateSha256":"6fdb921050e7bcc2e702f8487312ab42f48a34f27d5a11bf95c59e1b16a05f77","sourceState":"calendar-source-state.json","sourceStateSha256":"48f751a88674602499058bcbea04acbfbd61c91f5166ea5cc7ef051c9f6ae8ce"});
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
