(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.ca728da876cd9426.js","sha256":"ca728da876cd9426cafaf0c9ba3b617eda17f7ad77b39d97cb5cc9354ea98e28","count":2167,"publishedAt":"2026-10-14T17:20:06Z","state":"calendar-state.json","stateSha256":"6baf30f8c08bef024f863cc4bcd6d09684b814c4f5547895479d11fafc774112","sourceState":"calendar-source-state.json","sourceStateSha256":"b00688b5a693e465b32a8614ccffe7b5d3d7c91d06cc820f163b33d1cf0faedf"});
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
