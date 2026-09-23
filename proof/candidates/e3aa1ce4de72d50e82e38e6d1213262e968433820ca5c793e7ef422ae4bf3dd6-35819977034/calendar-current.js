(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.e3aa1ce4de72d50e.js","sha256":"e3aa1ce4de72d50e82e38e6d1213262e968433820ca5c793e7ef422ae4bf3dd6","count":2123,"publishedAt":"2026-09-23T04:51:00Z","state":"calendar-state.json","stateSha256":"ec1565e62de417b8d009b6388f25bcb47f2c2ce0893bd8bbc4bd544e58472f66","sourceState":"calendar-source-state.json","sourceStateSha256":"c69b6984c7c9150d69d7ffe640269258838a06c27fea5136a5f6b9648272f02c"});
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
