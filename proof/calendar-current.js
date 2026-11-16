(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.e85aebf6ea43db41.js","sha256":"e85aebf6ea43db41e7736bdd514b54d338852a0571d185f0aa73eefac1f48626","count":2096,"publishedAt":"2026-11-16T13:23:59Z","state":"calendar-state.json","stateSha256":"0b1830de34165158bb7bf4a842c74528a7e90ca1974338ea3f594329914788fb","sourceState":"calendar-source-state.json","sourceStateSha256":"b2d90221df7b04139713157618bdf5b52a11b78ee245358f46226dffa1c43902"});
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
