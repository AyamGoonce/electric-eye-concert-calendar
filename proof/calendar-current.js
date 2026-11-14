(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.390f0ece4d711837.js","sha256":"390f0ece4d7118375b3983e691834aaea471a671354d095f99bf2d7a2041cc18","count":2137,"publishedAt":"2026-11-14T00:06:28Z","state":"calendar-state.json","stateSha256":"b13ca88bb36e3e475107f02061fafa7eed5848ed59f8440bf85f2a9e3aec8825","sourceState":"calendar-source-state.json","sourceStateSha256":"cc2f350872f948ff28035db07fdd9741e1de153b1f5defefe66492eb57627123"});
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
