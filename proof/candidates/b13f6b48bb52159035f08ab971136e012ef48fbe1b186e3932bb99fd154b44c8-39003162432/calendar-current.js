(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.b13f6b48bb521590.js","sha256":"b13f6b48bb52159035f08ab971136e012ef48fbe1b186e3932bb99fd154b44c8","count":2100,"publishedAt":"2026-10-17T04:38:32Z","state":"calendar-state.json","stateSha256":"464cefb89ada38dcbbf784d88a43f4ecb1853ceb9fdb476eab9d3f133b56af6a","sourceState":"calendar-source-state.json","sourceStateSha256":"3883afad2a8e4f937143260825ccb3d5d88ba0803080e0d06017db8da4315afa"});
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
