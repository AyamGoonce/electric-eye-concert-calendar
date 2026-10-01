(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.7f10db8c88841b8a.js","sha256":"7f10db8c88841b8aac6273414e92adf4d1e22958c2f87a0c1ceae9866f29e441","count":2224,"publishedAt":"2026-10-01T10:29:06Z","state":"calendar-state.json","stateSha256":"2e18ba26f7cc8830b5535bb47b763c19c285edf1eef73cf57f48de95ef4c626c","sourceState":"calendar-source-state.json","sourceStateSha256":"62e113e83f9dd753e988150866398e0abebb7d435a48e870f55eaab7ac088ca3"});
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
