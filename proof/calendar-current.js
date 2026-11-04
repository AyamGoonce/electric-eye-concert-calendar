(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.86078137e3230999.js","sha256":"86078137e323099944803c476c46d7ee6477d9f27205988aaa0819bf857f064d","count":2047,"publishedAt":"2026-11-04T17:55:34Z","state":"calendar-state.json","stateSha256":"0812c23c226a868ab3184c840f85ea3a249dfee960329c698ba131603515ab3c","sourceState":"calendar-source-state.json","sourceStateSha256":"898e5d6c9d633591d2feee54425d85694d04c7e1bc5c00370dff9749f44dc556"});
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
